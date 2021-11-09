#include "ip_esp32.h"
#include "con_gear.h"
#include "bsp_usart.h"

uint8_t receive_array2[Array_Length] = { 0xFF , 0xFF , 0xFF };//��ʱ�洢����
uint8_t receive_length2 = 0;//��ǰ�洢λ��
uint8_t receive_valid2 = 0;//��ǰ�洢״̬

//Э�鶨����
uint8_t self_check_enable = 0;//��ʼ��������
uint8_t config_complete[Array_Length]								= { 0x7A , 0x91 , 0x85 };//��ʼ�����
uint8_t self_check_command[Array_Length]						=	{ 0x7A , 0xFF , 0x85 };//��ѯ��λ��
uint8_t sleep_warning[Array_Length]									=	{ 0x7A , 0xEE , 0x85 };//���߾���
extern uint8_t rudder_rotate_move[Array_Length];														 //���ǰ��ת��

void Decode2(void)
{
	if(Array_Comparation(receive_array2,config_complete)){Usart_SendArray(USART2,config_complete,Array_Length);}
	else if(Array_Comparation(receive_array2,self_check_command)){Usart_SendArray(USART1,self_check_command,Array_Length);}
	else if(Array_Comparation(receive_array2,rudder_rotate_move)){Usart_SendArray(USART1,rudder_rotate_move,Array_Length);}
	receive_array2[0] = 0xFF;
	receive_array2[1] = 0xFF;
	receive_array2[2] = 0xFF;
}

void USART2_IRQHandler(void)
{
	if(USART_GetITStatus(DEBUG_USART2x,USART_IT_RXNE) == SET)
	{
		uint8_t receive = USART_ReceiveData(USART2);
		USART_ClearITPendingBit(USART2,USART_IT_RXNE);
		if(receive_valid2 == 1)//�Ƿ���ɽ���
		{
			receive_array2[receive_length2] = receive;
			receive_length2++;
			if(Array_Length == receive_length2)
			{
				Decode2();
				receive_valid2 = 0;
				receive_length2 = 0;
			}
		}
		else 
		{
			if(receive == 0x7A)
			{
				receive_valid2 = 1;
				receive_length2 = 1;
				receive_array2[0] = 0x7A;
			}
		}
	}
}

/*********************************************END OF FILE**********************/
